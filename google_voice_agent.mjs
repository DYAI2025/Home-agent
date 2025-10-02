import 'dotenv/config';
import {
  AutoSubscribe,
  WorkerOptions,
  cli,
  defineAgent,
  log,
  voice,
} from '@livekit/agents';
import { turnDetector } from '@livekit/agents-plugin-livekit';
import * as google from '@livekit/agents-plugin-google';
import * as silero from '@livekit/agents-plugin-silero';
import { fileURLToPath } from 'node:url';

const logger = log();

const DEFAULT_AGENT_PROMPT =
  process.env.AGENT_INSTRUCTIONS ??
  'You are a proactive home cockpit assistant. Keep replies concise, speak clearly, and mention follow-up actions when helpful.';
const DEFAULT_SESSION_GREETING =
  process.env.AGENT_GREETING ??
  'Hello! I am ready to assist you with voice and avatar control.';

const LIVEKIT_URL = process.env.LIVEKIT_URL;
if (!LIVEKIT_URL) {
  throw new Error('LIVEKIT_URL is required. Example: wss://your-livekit-domain');
}

const normalizedLivekitUrl = (() => {
  if (LIVEKIT_URL.startsWith('ws://') || LIVEKIT_URL.startsWith('wss://')) {
    return LIVEKIT_URL;
  }
  if (LIVEKIT_URL.startsWith('https://')) {
    return 'wss://' + LIVEKIT_URL.slice('https://'.length);
  }
  if (LIVEKIT_URL.startsWith('http://')) {
    return 'ws://' + LIVEKIT_URL.slice('http://'.length);
  }
  throw new Error(
    `LIVEKIT_URL must be a websocket endpoint (wss://...). Received: ${LIVEKIT_URL}`,
  );
})();

const GOOGLE_REALTIME_MODEL = process.env.GOOGLE_REALTIME_MODEL;
if (!GOOGLE_REALTIME_MODEL) {
  throw new Error(
    'GOOGLE_REALTIME_MODEL is required for the Google realtime agent (example: gemini-2.0-flash-exp).',
  );
}

const DEFAULT_GOOGLE_VOICE = process.env.GOOGLE_GEMINI_VOICE ?? 'Puck';

export default defineAgent({
  prewarm: async (proc) => {
    // Cache the Silero VAD so individual jobs start faster.
    proc.userData ||= {};
    proc.userData.vad = await silero.VAD.load();
  },
  entry: async (ctx) => {
    logger.info('Launching Google Realtime voice session', {
      roomName: ctx.job?.metadata?.room ?? ctx.room.name,
      workerId: ctx.workerId,
    });

    // Ensure we are connected to the LiveKit room and subscribed to audio tracks.
    await ctx.connect(undefined, AutoSubscribe.AUDIO_ONLY);

    const vad = ctx.proc.userData?.vad ?? (await silero.VAD.load());

    const realtimeModel = new google.beta.realtime.RealtimeModel({
      model: GOOGLE_REALTIME_MODEL,
      voice: DEFAULT_GOOGLE_VOICE,
      apiKey: process.env.GOOGLE_API_KEY ?? process.env.GOOGLE_GENAI_API_KEY,
      instructions:
        process.env.GOOGLE_SESSION_INSTRUCTIONS ??
        'You are the spoken persona of a Ready Player Me avatar. Respond with warmth and stay action oriented.',
    });

    const session = new voice.AgentSession({
      vad,
      llm: realtimeModel,
      turnDetection: new turnDetector.EnglishModel(),
    });

    const assistant = new voice.Agent({ instructions: DEFAULT_AGENT_PROMPT });

    const localParticipant = ctx.room.localParticipant;
    const publishChat = async (text) => {
      if (!localParticipant) return;
      const message = text?.trim();
      if (!message) return;
      try {
        await localParticipant.publishData(Buffer.from(message, 'utf-8'), {
          reliable: true,
          topic: 'chat',
        });
      } catch (err) {
        logger.warn({ err }, 'Failed to publish chat packet');
      }
    };

    session.on('user_input_transcribed', (event) => {
      if (event.isFinal) {
        logger.info({ transcript: event.transcript, speaker: event.speakerId }, 'User input received');
      }
    });

    session.on('error', (event) => {
      logger.error({ err: event.error }, 'Agent session reported an error');
    });

    await publishChat('Agent connected. Preparing Gemini realtime session.');

    try {
      await session.start({
        agent: assistant,
        room: ctx.room,
        outputOptions: { transcriptionEnabled: true },
      });

      await session.say(DEFAULT_SESSION_GREETING);

      await new Promise((resolve) => {
        session.once('close', resolve);
        ctx.room.once('disconnected', resolve);
      });
    } finally {
      await publishChat('Agent session finished.');
      try {
        await session.aclose();
      } catch (err) {
        logger.debug({ err }, 'Agent session already closed');
      }
    }
  },
});

const concurrency = Number.parseInt(process.env.LIVEKIT_AGENT_CONCURRENCY ?? '1', 10) || 1;

cli.runApp(
  new WorkerOptions({
    agent: fileURLToPath(import.meta.url),
    wsUrl: normalizedLivekitUrl,
    apiKey: process.env.LIVEKIT_API_KEY,
    apiSecret: process.env.LIVEKIT_API_SECRET,
    concurrency,
  }),
);

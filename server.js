// server.js - Node.js server to serve the avatar cockpit
const express = require('express');
const http = require('http');
const path = require('path');
const { AccessToken } = require('livekit-server-sdk');

const app = express();
const server = http.createServer(app);

const READY_PLAYER_ME_SUBDOMAIN = process.env.READY_PLAYER_ME_SUBDOMAIN || 'demo';
const LIVEKIT_URL = process.env.LIVEKIT_URL || 'ws://localhost:7880';

app.use(express.json());

app.get('/config.js', (_req, res) => {
  res
    .type('application/javascript')
    .send(
      `window.RUNTIME = ${JSON.stringify({
        READY_PLAYER_ME_SUBDOMAIN,
        LIVEKIT_URL,
      })};`
    );
});

// Serve static files from the current directory
app.use(express.static(path.join(__dirname)));

// Endpoint to generate access tokens for clients
app.get('/token', (req, res) => {
  const API_KEY = process.env.LIVEKIT_API_KEY;
  const API_SECRET = process.env.LIVEKIT_API_SECRET;
  const room = req.query.room || 'default-room';
  const participantIdentity = req.query.identity || `participant-${Date.now()}`;

  if (!API_KEY || !API_SECRET) {
    return res.status(500).json({
      error: 'Missing LIVEKIT_API_KEY or LIVEKIT_API_SECRET',
    });
  }

  try {
    const at = new AccessToken(API_KEY, API_SECRET, {
      identity: participantIdentity,
    });

    at.addGrant({ room, roomJoin: true, canPublish: true, canSubscribe: true });

    res.json({
      token: at.toJwt(),
      url: LIVEKIT_URL,
      room,
    });
  } catch (error) {
    console.error('Token generation failed:', error);
    res.status(500).json({ error: 'Unable to create LiveKit token' });
  }
});

const port = process.env.PORT || 3000;
server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
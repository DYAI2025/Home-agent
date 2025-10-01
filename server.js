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
  res.type('application/javascript').send(`window.RUNTIME = ${JSON.stringify({
    READY_PLAYER_ME_SUBDOMAIN,
    LIVEKIT_URL,
  })};`);
});

app.use(express.static(path.join(__dirname)));

app.get('/token', (req, res) => {
  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const room = req.query.room || 'default-room';
  const participantIdentity = req.query.identity || `participant-${Date.now()}`;

  if (!apiKey || !apiSecret) {
    return res.status(500).send('Missing LIVEKIT_API_KEY or LIVEKIT_API_SECRET');
  }

  const token = new AccessToken(apiKey, apiSecret, {
    identity: participantIdentity,
  });

  token.addGrant({ room, roomJoin: true, canPublish: true, canSubscribe: true });

  res.json({
    token: token.toJwt(),
    url: LIVEKIT_URL,
    room,
  });
});

const port = Number(process.env.PORT || 3000);
server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

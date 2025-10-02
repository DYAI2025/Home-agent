Place LiveKit browser bundles here when deploying in environments without CDN access.

Required files (matching index.html fallbacks):
- livekit-client.esm.mjs
- livekit-client.umd.min.js

You can obtain them from the livekit-client npm package:
  npm install livekit-client@2.15.7
  cp node_modules/livekit-client/dist/livekit-client.esm.mjs libs/
  cp node_modules/livekit-client/dist/livekit-client.umd.min.js libs/

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    res.end("Method Not Allowed");
    return;
  }

  const agentName = process.env.PIPECAT_AGENT_NAME;
  const apiKey = process.env.PIPECAT_PUBLIC_API_KEY;
  const apiBase =
    process.env.PIPECAT_CLOUD_API_BASE ||
    "https://api.pipecat.daily.co/v1/public";

  if (!agentName || !apiKey) {
    res.statusCode = 500;
    res.end("Missing PIPECAT_AGENT_NAME or PIPECAT_PUBLIC_API_KEY");
    return;
  }

  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch (err) {
      res.statusCode = 400;
      res.end("Invalid JSON body");
      return;
    }
  }

  const requestData =
    body && typeof body === "object" && body.requestData
      ? { ...body.requestData }
      : {};

  // Enforce Daily transport for Cloud sessions.
  requestData.transport = "daily";
  requestData.createDailyRoom = true;
  if (requestData.enableDefaultIceServers === undefined) {
    requestData.enableDefaultIceServers = true;
  }

  const endpoint = `${apiBase}/${encodeURIComponent(agentName)}/start`;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    const text = await response.text();
    res.statusCode = response.status;
    res.setHeader("Content-Type", "application/json");
    res.end(text);
  } catch (err) {
    res.statusCode = 502;
    res.end("Failed to start Pipecat session");
  }
}

export async function logToServer(level: string, message: string, data?: any) {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api"}/log`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ level, message, data }),
    });
    if (!res.ok) {
      console.error("Failed to send log to server:", res.status);
    }
  } catch (err) {
    console.error("Error sending log to server:", err);
  }
}

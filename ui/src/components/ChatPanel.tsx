"use client";

import { useState, useRef, useEffect } from "react";
import { mockChatMessages } from "@/lib/mock-data";
import { ChatMessage } from "@/lib/types";
import { Send } from "lucide-react";

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);
    setStreamingContent("");

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: input }),
        }
      );

      if (res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = decoder.decode(value, { stream: true });
          const lines = text.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") continue;
              fullContent += data;
              setStreamingContent(fullContent);
            }
          }
        }

        const aiMsg: ChatMessage = {
          id: `msg-${Date.now()}`,
          role: "ai",
          content: fullContent || "I'll analyze that pattern and get back to you with recommendations.",
        };
        setMessages((prev) => [...prev, aiMsg]);
      } else {
        // Fallback: mock streaming
        const mockResponse =
          "Based on my analysis, I can see the pattern you're describing. Let me coordinate with the swarm to investigate further and provide a detailed recommendation.";
        let idx = 0;
        const interval = setInterval(() => {
          if (idx < mockResponse.length) {
            setStreamingContent(mockResponse.slice(0, idx + 1));
            idx++;
          } else {
            clearInterval(interval);
            setMessages((prev) => [
              ...prev,
              {
                id: `msg-${Date.now()}`,
                role: "ai",
                content: mockResponse,
              },
            ]);
            setStreamingContent("");
            setIsStreaming(false);
          }
        }, 30);
        return;
      }
    } catch {
      // Fallback mock streaming
      const mockResponse =
        "Based on my analysis, I can see the pattern you're describing. Let me coordinate with the swarm to investigate further.";
      let idx = 0;
      const interval = setInterval(() => {
        if (idx < mockResponse.length) {
          setStreamingContent(mockResponse.slice(0, idx + 1));
          idx++;
        } else {
          clearInterval(interval);
          setMessages((prev) => [
            ...prev,
            {
              id: `msg-${Date.now()}`,
              role: "ai",
              content: mockResponse,
            },
          ]);
          setStreamingContent("");
          setIsStreaming(false);
        }
      }, 30);
      return;
    }

    setStreamingContent("");
    setIsStreaming(false);
  };

  return (
    <section
      className="rounded-xl overflow-hidden flex flex-col stagger-3"
      style={{
        background: "var(--bg-elev)",
        border: "1px solid var(--border)",
        height: "540px",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-6 py-[18px]"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <div className="flex items-center gap-2.5">
          <span
            className="text-[22px] tracking-tight"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Ask the Swarm
          </span>
        </div>
        <span
          className="text-[11px] uppercase tracking-widest"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-dim)",
            letterSpacing: "0.1em",
          }}
        >
          · Gemini 2.5 Pro
        </span>
      </div>

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-4"
      >
        {messages.map((msg) => (
          <div key={msg.id} className="flex gap-2.5">
            {/* Avatar */}
            <div
              className="w-[26px] h-[26px] rounded-md shrink-0 flex items-center justify-center text-[10px] font-semibold"
              style={{
                fontFamily: "var(--font-mono)",
                ...(msg.role === "user"
                  ? {
                      background:
                        "linear-gradient(135deg, #6ea8ff, #b794f6)",
                      color: "white",
                    }
                  : {
                      background: "var(--accent)",
                      color: "var(--bg)",
                    }),
              }}
            >
              {msg.role === "user" ? "RK" : "E"}
            </div>

            {/* Bubble */}
            <div className="flex-1 text-[13px] leading-relaxed" style={{ color: "var(--text)" }}>
              <div
                dangerouslySetInnerHTML={{
                  __html: msg.content.replace(
                    /<code>(.*?)<\/code>/g,
                    '<code style="font-family:var(--font-mono);font-size:11px;background:var(--surface);padding:1px 5px;border-radius:3px;color:var(--accent)">$1</code>'
                  ),
                }}
              />
              {msg.reasoning && (
                <div
                  className="mt-2 px-3 py-2.5 rounded-r-md text-[12px] leading-relaxed italic"
                  style={{
                    background: "var(--surface)",
                    borderLeft: "2px solid var(--accent)",
                    color: "var(--text-muted)",
                  }}
                >
                  {msg.reasoning}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Streaming message */}
        {isStreaming && (
          <div className="flex gap-2.5">
            <div
              className="w-[26px] h-[26px] rounded-md shrink-0 flex items-center justify-center text-[10px] font-semibold"
              style={{
                fontFamily: "var(--font-mono)",
                background: "var(--accent)",
                color: "var(--bg)",
              }}
            >
              E
            </div>
            <div
              className="flex-1 text-[13px] leading-relaxed"
              style={{ color: "var(--text)" }}
            >
              {streamingContent || (
                <span className="flex gap-1">
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{
                      background: "var(--text-muted)",
                      animation: "typingDot 1.4s ease-in-out infinite",
                    }}
                  />
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{
                      background: "var(--text-muted)",
                      animation: "typingDot 1.4s ease-in-out 0.2s infinite",
                    }}
                  />
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{
                      background: "var(--text-muted)",
                      animation: "typingDot 1.4s ease-in-out 0.4s infinite",
                    }}
                  />
                </span>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        className="flex items-center gap-2.5 px-4 py-3.5"
        style={{
          borderTop: "1px solid var(--border)",
          background: "var(--surface)",
        }}
      >
        <span
          style={{
            color: "var(--accent)",
            fontFamily: "var(--font-mono)",
          }}
        >
          ›
        </span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask anything about your data estate…"
          className="flex-1 bg-transparent border-none outline-none text-[13px] p-1"
          style={{
            color: "var(--text)",
            fontFamily: "var(--font-body)",
          }}
          disabled={isStreaming}
        />
        <button
          onClick={handleSend}
          className="w-7 h-7 rounded-md flex items-center justify-center cursor-pointer transition-opacity"
          style={{
            background: "var(--accent)",
            border: "none",
            color: "var(--bg)",
            opacity: isStreaming ? 0.5 : 1,
          }}
          disabled={isStreaming}
          aria-label="Send message"
        >
          <Send size={14} />
        </button>
      </div>
    </section>
  );
}

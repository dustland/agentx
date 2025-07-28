"use client";

import { MessageParts, type MessagePart } from "./chat/message-parts";

// Test data
const testParts: MessagePart[] = [
  {
    type: "text",
    text: "I'll help you analyze the weather data for Tokyo."
  },
  {
    type: "tool-call",
    toolCallId: "tc_weather_123",
    toolName: "get_weather",
    args: { location: "Tokyo", units: "celsius" },
    status: "completed"
  },
  {
    type: "tool-result",
    toolCallId: "tc_weather_123",
    toolName: "get_weather",
    result: {
      temperature: 22,
      condition: "Partly cloudy",
      humidity: 65
    },
    isError: false
  },
  {
    type: "text",
    text: "Based on the data:\n- Temperature: 22°C\n- Conditions: Partly cloudy\n- Humidity: 65%"
  }
];

export function TestMessageParts() {
  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold">Message Parts Test</h1>
      
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Complete Message</h2>
        <MessageParts parts={testParts} isStreaming={false} />
      </div>
      
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Streaming Message</h2>
        <MessageParts parts={testParts.slice(0, 2)} isStreaming={true} />
      </div>
      
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Error Example</h2>
        <MessageParts 
          parts={[
            { type: "text", text: "Let me check the database..." },
            { 
              type: "tool-call", 
              toolCallId: "tc_db_456",
              toolName: "database_query",
              args: { query: "SELECT * FROM users" },
              status: "failed"
            },
            {
              type: "tool-result",
              toolCallId: "tc_db_456",
              toolName: "database_query",
              result: "Connection timeout",
              isError: true
            },
            {
              type: "error",
              error: "Failed to connect to database",
              errorCode: "DB_TIMEOUT"
            }
          ]} 
          isStreaming={false} 
        />
      </div>
    </div>
  );
}
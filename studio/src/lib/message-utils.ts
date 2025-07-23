import { ChatMessage } from "@/types/chat";
import { Message, MessageContent } from "@/types/vibex";

/**
 * Convert legacy ChatMessage to new Message format
 */
export function chatMessageToMessage(chatMessage: ChatMessage): Message {
  const content: MessageContent[] = [];
  
  // Add text content
  if (chatMessage.content) {
    content.push({
      type: "text",
      text: chatMessage.content,
    });
  }
  
  // Add tool calls if present
  if (chatMessage.metadata?.toolCalls) {
    chatMessage.metadata.toolCalls.forEach((toolCall, index) => {
      content.push({
        type: "tool-call",
        toolCallId: `${chatMessage.id}-tool-${index}`,
        toolName: toolCall.name,
        args: toolCall.parameters || {},
      });
      
      if (toolCall.result !== undefined) {
        content.push({
          type: "tool-result",
          toolCallId: `${chatMessage.id}-tool-${index}`,
          toolName: toolCall.name,
          result: toolCall.result,
          isError: toolCall.status === "error",
        });
      }
    });
  }
  
  return {
    id: chatMessage.id,
    role: chatMessage.role === "assistant" ? "assistant" : chatMessage.role,
    content: content.length === 1 && content[0].type === "text" 
      ? content[0].text 
      : content,
    timestamp: chatMessage.timestamp.toISOString(),
    metadata: {
      agentId: chatMessage.metadata?.agentId,
      agentName: chatMessage.metadata?.agentName,
    },
  };
}

/**
 * Convert new Message format to legacy ChatMessage for backward compatibility
 */
export function messageToChatMessage(message: Message): ChatMessage {
  let content = "";
  const toolCalls: any[] = [];
  
  if (typeof message.content === "string") {
    content = message.content;
  } else if (Array.isArray(message.content)) {
    message.content.forEach(part => {
      if (part.type === "text") {
        content += part.text;
      } else if (part.type === "tool-call") {
        toolCalls.push({
          name: part.toolName,
          status: "running",
          parameters: part.args,
        });
      } else if (part.type === "tool-result") {
        const toolCall = toolCalls.find(tc => tc.name === part.toolName);
        if (toolCall) {
          toolCall.status = part.isError ? "error" : "completed";
          toolCall.result = part.result;
        }
      }
    });
  } else if (message.content.type === "text") {
    content = message.content.text;
  }
  
  return {
    id: message.id,
    role: message.role as "user" | "assistant" | "system",
    content,
    timestamp: new Date(message.timestamp),
    status: "complete",
    metadata: {
      ...message.metadata,
      toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
    },
  };
}
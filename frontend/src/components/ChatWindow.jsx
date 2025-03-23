import React from "react";
import Message from "./Message";
import TypingIndicator from "./TypingIndicator";

const ChatWindow = ({ messages, isLoading }) => {
  return (
    <div
      style={{
        padding: "20px",
        backgroundColor: "rgba(0, 55, 123, 0.93)",
        borderRadius: "10px",
        minHeight: "500px",
      }}
    >
      {messages.map((msg, index) => (
        <Message key={index} text={msg.text} from={msg.from} />
      ))}
      {isLoading && <TypingIndicator />}
    </div>
  );
};

export default ChatWindow;

import React from "react";

const Message = ({ text, from }) => {
  const isUser = from === "user";
  return (
    <div style={{ textAlign: isUser ? "right" : "left", margin: "10px" }}>
      <div
        style={{
          display: "inline-block",
          backgroundColor: isUser ? "#0055a2" : "#fff",
          color: isUser ? "#fff" : "#333",
          padding: "10px",
          borderRadius: "10px",
          maxWidth: "70%",
        }}
      >
        {text}
      </div>
    </div>
  );
};

export default Message;

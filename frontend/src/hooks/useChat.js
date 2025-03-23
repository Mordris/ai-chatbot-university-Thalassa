import { useState } from "react";
import axios from "axios";

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message) => {
    // Add user message to the chat
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: message, from: "user" },
    ]);
    setIsLoading(true);

    try {
      // Make sure you're calling the correct backend URL (http://localhost:8000)
      const response = await axios.get("http://localhost:8000/chat", {
        params: { query: message },
      });

      // Add the bot's response to the chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: response.data.answer, from: "bot" }, // Bot response
      ]);
    } catch (error) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "Sorry, something went wrong.", from: "bot" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, sendMessage, isLoading };
};

export default useChat;

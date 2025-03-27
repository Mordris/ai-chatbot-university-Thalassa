import { useState, useCallback } from "react";
import axios from "axios";
import debounce from "lodash.debounce";

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(
    debounce(async (message) => {
      setMessages((prev) => [...prev, { text: message, from: "user" }]);
      setIsLoading(true);

      try {
        const response = await axios.get("http://localhost:8000/chat", {
          params: { query: message },
        });

        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { text: response.data.answer, from: "bot" },
          ]);
          setIsLoading(false);
        }, 1000);
      } catch (error) {
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { text: "Sorry, something went wrong.", from: "bot" },
          ]);
          setIsLoading(false);
        }, 1000);
      }
    }, 500), // 500ms debounce
    [] // Empty dependency array ensures it's only created once
  );

  return { messages, sendMessage, isLoading };
};

export default useChat;

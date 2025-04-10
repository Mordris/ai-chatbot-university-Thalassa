import { useState, useCallback, useRef } from "react"; // Import useRef
import axios from "axios";
import debounce from "lodash.debounce"; // Keep debounce if you like the typing delay effect

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  // Use useRef to store sessionId - it persists across renders without causing re-renders itself
  // Initialize with null. We'll update it after the first successful API call.
  const sessionIdRef = useRef(null);

  const sendMessage = useCallback(
    // Keep debounce if you prefer the effect, otherwise remove debounce() wrapper and timeout
    debounce(async (message) => {
      if (!message || message.trim() === "") return; // Prevent sending empty messages

      // Add user message immediately
      setMessages((prev) => [...prev, { text: message, from: "user" }]);
      setIsLoading(true); // Start loading indicator

      try {
        // Prepare parameters, including sessionId if it exists
        const params = { query: message };
        if (sessionIdRef.current) {
          params.session_id = sessionIdRef.current;
        }

        // Make the API call
        const response = await axios.get("http://localhost:8000/chat", {
          params,
        });

        // Process successful response
        if (response.data && response.data.answer) {
          // If this was the first message (sessionId was null), store the new sessionId from the backend
          if (!sessionIdRef.current && response.data.session_id) {
            sessionIdRef.current = response.data.session_id;
            console.log("Session started with ID:", sessionIdRef.current); // For debugging
          }

          // Add bot response
          setMessages((prev) => [
            ...prev,
            { text: response.data.answer, from: "bot" },
          ]);
        } else {
          // Handle case where backend responds 200 but without expected data
          console.error("Invalid response structure:", response.data);
          setMessages((prev) => [
            ...prev,
            {
              text: "Received an unexpected response from the server.",
              from: "bot",
            },
          ]);
        }
      } catch (error) {
        // Handle API errors
        console.error("API Error:", error.response || error.message); // Log detailed error
        let errorMessage = "Sorry, something went wrong.";
        if (
          error.response &&
          error.response.data &&
          error.response.data.detail
        ) {
          // Try to get specific error detail from FastAPI
          errorMessage = `Error: ${error.response.data.detail}`;
        } else if (error.request) {
          // Handle network errors (couldn't reach server)
          errorMessage =
            "Sorry, I couldn't connect to the server. Please check your connection.";
        }
        setMessages((prev) => [...prev, { text: errorMessage, from: "bot" }]);
      } finally {
        // Stop loading indicator regardless of success or failure
        setIsLoading(false);
      }
    }, 300), // Adjust debounce time as needed (e.g., 300ms)
    [] // Keep empty dependency array for useCallback
  );

  return { messages, sendMessage, isLoading };
};

export default useChat;

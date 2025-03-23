import axios from "axios";

export const fetchAnswer = async (query) => {
  try {
    const response = await axios.get("/chat", { params: { query } });
    return response.data.answer;
  } catch (error) {
    console.error("API error:", error);
    return "Sorry, there was an issue with the request.";
  }
};

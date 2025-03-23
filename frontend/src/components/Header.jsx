import React from "react";
import { Typography } from "@mui/material";

const Header = () => (
  <div
    style={{
      padding: "20px",
      backgroundColor: "#00377B",
      textAlign: "center",
      borderRadius: "10px",
    }}
  >
    {/* Add the image here */}
    <img
      src="/thalassa.png" // This path is relative to the public folder
      alt="Thalassa AI"
      style={{
        width: "100px", // Adjust size as needed
        height: "auto",
        marginBottom: "15px", // Space between the image and the title
      }}
    />
    <Typography variant="h4" style={{ color: "#fff" }}>
      Thalassa
    </Typography>
    <Typography variant="h5" style={{ color: "#fff" }}>
      Sakarya University AI Assistant
    </Typography>
  </div>
);

export default Header;

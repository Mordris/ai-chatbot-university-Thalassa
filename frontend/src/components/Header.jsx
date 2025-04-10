// In Header.js
import React from "react";
import { Typography, Box } from "@mui/material"; // Use Box for layout

const Header = () => (
  <Box // Use Box instead of div
    sx={{
      // Use sx prop
      padding: 3, // Use theme spacing units (default 8px)
      backgroundColor: "primary.dark", // Use theme colors (adjust if needed)
      textAlign: "center",
      borderRadius: 2, // Use theme border radius units
      mb: 2, // Add margin bottom
    }}
  >
    <Box // Nested Box for the image
      component="img"
      src="/thalassa.png"
      alt="Thalassa AI"
      sx={{
        width: 100,
        height: "auto",
        mb: 2,
      }}
    />
    <Typography variant="h4" sx={{ color: "#fff", fontWeight: "bold" }}>
      {" "}
      {/* Add fontWeight */}
      Thalassa
    </Typography>
    <Typography variant="h6" sx={{ color: "#fff" }}>
      {" "}
      {/* Maybe h6 is better */}
      Sakarya University AI Assistant
    </Typography>
  </Box>
);

export default Header;

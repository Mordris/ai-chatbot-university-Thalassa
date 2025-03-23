import React from "react";
import { Fade } from "@mui/material";
import { CircleLoader } from "react-spinners";

const TypingIndicator = () => (
  <div style={{ textAlign: "center", marginTop: "20px" }}>
    <Fade in={true} timeout={1000}>
      <div>
        <CircleLoader color="#fff" size={50} />
        <span style={{ color: "#fff", marginLeft: "10px" }}>Writing...</span>
      </div>
    </Fade>
  </div>
);

export default TypingIndicator;

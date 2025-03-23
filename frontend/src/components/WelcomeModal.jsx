import React from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
} from "@mui/material";

const WelcomeModal = ({ open, onClose }) => (
  <Dialog open={open} onClose={onClose}>
    <DialogTitle>Welcome to the AI Chatbot</DialogTitle>
    <DialogContent>
      <p>
        Note: The AI might make mistakes. Please be aware of that while
        chatting!
      </p>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose} color="primary">
        OK
      </Button>
    </DialogActions>
  </Dialog>
);

export default WelcomeModal;

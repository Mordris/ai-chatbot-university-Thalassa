import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "rgba(0, 55, 123, 0.93)",
    },
    background: {
      default: "#efeae4",
    },
  },
  typography: {
    fontFamily: "Arial, sans-serif",
  },
});

export default theme;

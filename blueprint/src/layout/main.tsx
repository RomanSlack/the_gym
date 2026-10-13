import { createRoot } from "react-dom/client";
import "@fontsource/ibm-plex-sans-condensed/400.css";
import "@fontsource/ibm-plex-sans-condensed/600.css";
import "@fontsource/ibm-plex-mono/400.css";
import "./layout.css";
import LayoutApp from "./LayoutApp";

createRoot(document.getElementById("root")!).render(<LayoutApp />);

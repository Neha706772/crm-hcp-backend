import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { store } from "./store/store";
import LogInteractionScreen from "./components/LogInteractionScreen";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <LogInteractionScreen />
    </Provider>
  </React.StrictMode>
);
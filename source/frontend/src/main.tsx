import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import App from "./App.tsx";
import Dashboard      from "./pages/Dashboard.tsx";
import Environment    from "./pages/Environment.tsx";
import Power          from "./pages/Power.tsx";
import AirlockThermal from "./pages/AirlockThermal.tsx";
import Actuators      from "./pages/Actuators.tsx";
import Rules          from "./pages/Rules.tsx";
import Alerts         from "./pages/Alerts.tsx";

import "./index.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true,         element: <Dashboard />,      handle: { title: "Dashboard" } },
      { path: "environment", element: <Environment />,    handle: { title: "Environment" } },
      { path: "power",       element: <Power />,          handle: { title: "Power" } },
      { path: "airlock",     element: <AirlockThermal />, handle: { title: "Airlock & Thermal" } },
      { path: "actuators",   element: <Actuators />,      handle: { title: "Actuators" } },
      { path: "rules",       element: <Rules />,          handle: { title: "Rules" } },
      { path: "alerts",      element: <Alerts />,         handle: { title: "Alerts" } },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);

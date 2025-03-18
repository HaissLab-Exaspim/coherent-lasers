const isDev = import.meta.env.MODE === "development";
const host = isDev ? "localhost:8000" : window.location.host;
const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";

export const API_BASE = isDev ? `http://${ host }/api` : "/api";
export const WS_URL = `${ wsProtocol }://${ host }/ws`;

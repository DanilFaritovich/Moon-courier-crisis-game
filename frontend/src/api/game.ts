import type {
  AvailableOrder,
  GameState,
  MapPoint,
  MapRoad,
} from "../types/game";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? String(body.detail)
        : response.statusText;
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const gameApi = {
  state: () => request<GameState>("/game/state"),
  map: () => request<{ points: MapPoint[]; roads: MapRoad[] }>("/game/map"),
  nextTurn: () => request<GameState>("/game/next-turn", { method: "POST" }),
  availableOrders: (roverId: number) =>
    request<AvailableOrder[]>(`/game/rovers/${roverId}/available-orders`),
  createDelivery: (roverId: number, orderId: number) =>
    request<GameState>("/game/deliveries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rover_id: roverId, order_id: orderId }),
    }),
  cancelDelivery: (deliveryId: number) =>
    request<GameState>(`/game/deliveries/${deliveryId}`, { method: "DELETE" }),
};

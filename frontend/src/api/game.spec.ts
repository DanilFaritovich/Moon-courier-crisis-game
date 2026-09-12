import { afterEach, describe, expect, it, vi } from "vitest";
import { gameApi } from "./game";

describe("gameApi", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("sends rover and order ids when creating a delivery", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          game_id: "game",
          active_rovers: [],
          active_orders: [],
          active_deliveries: [],
          active_events: [],
          turn: 1,
          money: 0,
          score: 0,
        }),
        { status: 200 },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await gameApi.createDelivery(4, 9);

    expect(fetchMock).toHaveBeenCalledWith(
      "/game/deliveries",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ rover_id: 4, order_id: 9 }),
      }),
    );
  });

  it("returns the backend detail for failed requests", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(
            JSON.stringify({ detail: "Rover 4 is not available." }),
            { status: 409 },
          ),
        ),
    );

    await expect(gameApi.createDelivery(4, 9)).rejects.toThrow(
      "Rover 4 is not available.",
    );
  });

  it("uses the expected endpoints for cancellation and the next turn", async () => {
    const gameState = {
      game_id: "game",
      active_rovers: [],
      active_orders: [],
      active_deliveries: [],
      active_events: [],
      turn: 2,
      money: 0,
      score: 0,
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify(gameState), { status: 200 }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify(gameState), { status: 200 }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await gameApi.cancelDelivery(11);
    await gameApi.nextTurn();

    expect(fetchMock).toHaveBeenNthCalledWith(1, "/game/deliveries/11", {
      method: "DELETE",
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/game/next-turn", {
      method: "POST",
    });
  });
});

import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

const gameApi = vi.hoisted(() => ({
  state: vi.fn(),
  map: vi.fn(),
  nextTurn: vi.fn(),
  cancelDelivery: vi.fn(),
  availableOrders: vi.fn(),
  createDelivery: vi.fn(),
}));
vi.mock("../api/game", () => ({ gameApi }));
import GameView from "./GameView.vue";

const state = {
  game_id: "game",
  active_rovers: [
    {
      id: 1,
      name: "Artemis-1",
      battery: 100,
      battery_capacity: 100,
      cargo: 0,
      cargo_capacity: 20,
      current_point_id: 1,
      status: "idle" as const,
    },
  ],
  active_orders: [],
  active_deliveries: [],
  active_events: [],
  turn: 1,
  money: 0,
  score: 0,
};

describe("GameView", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    gameApi.state.mockResolvedValue(state);
    gameApi.map.mockResolvedValue({
      points: [{ id: 1, name: "Lunar Base", type: "base", x: 0, y: 0 }],
      roads: [],
    });
  });

  it("loads game state and refreshes it after Next Turn", async () => {
    const nextState = { ...state, turn: 2, money: 60 };
    gameApi.nextTurn.mockResolvedValue(nextState);
    const wrapper = mount(GameView, {
      global: {
        stubs: { GameMap: true, GameInfoPanel: true, RoverDock: true },
      },
    });
    await flushPromises();
    expect(wrapper.text()).toContain("1");
    await wrapper.findComponent({ name: "TopBar" }).vm.$emit("nextTurn");
    await flushPromises();
    expect(gameApi.nextTurn).toHaveBeenCalledOnce();
    expect(wrapper.text()).toContain("2");
  });

  it("cancels a delivery emitted by the rover dock", async () => {
    const withDelivery = {
      ...state,
      active_deliveries: [
        {
          id: 7,
          order_id: 3,
          rover_id: 1,
          status: "in_progress" as const,
          started_turn: 1,
          completed_turn: null,
        },
      ],
    };
    gameApi.state.mockResolvedValue(withDelivery);
    gameApi.cancelDelivery.mockResolvedValue(state);
    const wrapper = mount(GameView, {
      global: {
        stubs: {
          GameMap: true,
          GameInfoPanel: true,
          RoverDock: {
            template:
              '<button class="dock-cancel" @click="$emit(\'cancel\', 7)" />',
          },
        },
      },
    });
    await flushPromises();
    await wrapper.get(".dock-cancel").trigger("click");
    await flushPromises();
    expect(gameApi.cancelDelivery).toHaveBeenCalledWith(7);
  });

  it("opens deployment confirmation for a single dropped contract", async () => {
    const order = {
      id: 3,
      destination_point_id: 2,
      weight: 3,
      reward: 60,
      urgency: "low" as const,
      status: "available" as const,
    };
    gameApi.state.mockResolvedValue({ ...state, active_orders: [order] });
    gameApi.availableOrders.mockResolvedValue([
      { ...order, distance: 11, battery_before: 100, battery_after: 67 },
    ]);
    const wrapper = mount(GameView, {
      global: {
        stubs: { GameMap: true, GameInfoPanel: true, RoverDock: true },
      },
    });
    await flushPromises();

    await wrapper
      .findComponent({ name: "RoverDock" })
      .vm.$emit("dragStart", state.active_rovers[0]);
    await flushPromises();
    await wrapper
      .findComponent({ name: "GameMap" })
      .vm.$emit("chooseOrders", [order]);
    await flushPromises();

    expect(wrapper.text()).toContain("CONFIRM DEPLOYMENT");
    expect(wrapper.text()).toContain("contract #3");
  });

  it("shows contract selection when multiple contracts are dropped", async () => {
    const orders = [
      {
        id: 3,
        destination_point_id: 2,
        weight: 3,
        reward: 60,
        urgency: "low" as const,
        status: "available" as const,
      },
      {
        id: 4,
        destination_point_id: 2,
        weight: 5,
        reward: 90,
        urgency: "high" as const,
        status: "available" as const,
      },
    ];
    gameApi.state.mockResolvedValue({ ...state, active_orders: orders });
    gameApi.availableOrders.mockResolvedValue(
      orders.map((order) => ({
        ...order,
        distance: 11,
        battery_before: 100,
        battery_after: 67,
      })),
    );
    const wrapper = mount(GameView, {
      global: {
        stubs: { GameMap: true, GameInfoPanel: true, RoverDock: true },
      },
    });
    await flushPromises();

    await wrapper
      .findComponent({ name: "RoverDock" })
      .vm.$emit("dragStart", state.active_rovers[0]);
    await flushPromises();
    await wrapper
      .findComponent({ name: "GameMap" })
      .vm.$emit("chooseOrders", orders);
    await flushPromises();

    expect(wrapper.text()).toContain("SELECT CONTRACT");
    expect(wrapper.text()).toContain("CONTRACT #3");
    expect(wrapper.text()).toContain("CONTRACT #4");
  });
});

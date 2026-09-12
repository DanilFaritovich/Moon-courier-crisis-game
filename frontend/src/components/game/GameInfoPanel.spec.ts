import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import GameInfoPanel from "./GameInfoPanel.vue";

describe("GameInfoPanel", () => {
  it("emits the selected delivery id when cancellation is requested", async () => {
    const wrapper = mount(GameInfoPanel, {
      props: {
        rover: {
          id: 1,
          name: "Artemis-1",
          battery: 67,
          battery_capacity: 100,
          cargo: 3,
          cargo_capacity: 20,
          current_point_id: 2,
          status: "delivering",
        },
        delivery: {
          id: 8,
          order_id: 4,
          rover_id: 1,
          status: "in_progress",
          started_turn: 1,
          completed_turn: null,
        },
        locationName: "Crater Alpha",
      },
    });

    expect(wrapper.text()).toContain("Crater Alpha");
    await wrapper.get("button").trigger("click");
    expect(wrapper.emitted("cancel")?.[0]).toEqual([8]);
  });

  it("shows contracts at a point and cancels the matching assigned delivery", async () => {
    const wrapper = mount(GameInfoPanel, {
      props: {
        point: { id: 2, name: "Crater Alpha", type: "delivery", x: 10, y: 5 },
        orders: [
          {
            id: 4,
            destination_point_id: 2,
            weight: 3,
            reward: 60,
            urgency: "low",
            status: "assigned",
          },
        ],
        deliveries: [
          {
            id: 9,
            order_id: 4,
            rover_id: 1,
            status: "in_progress",
            started_turn: 1,
            completed_turn: null,
          },
        ],
      },
    });
    expect(wrapper.text()).toContain("CONTRACT #4");
    await wrapper.get("button").trigger("click");
    expect(wrapper.emitted("cancel")?.[0]).toEqual([9]);
  });
});

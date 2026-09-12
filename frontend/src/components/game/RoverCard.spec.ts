import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import RoverCard from "./RoverCard.vue";

const baseRover = {
  id: 1,
  name: "Artemis-1",
  battery: 100,
  battery_capacity: 100,
  cargo: 0,
  cargo_capacity: 20,
  current_point_id: 1,
  status: "idle" as const,
};

describe("RoverCard", () => {
  it("allows an idle rover to be dragged", () => {
    const wrapper = mount(RoverCard, {
      props: { rover: baseRover, selected: false },
    });
    expect(wrapper.attributes("draggable")).toBe("true");
  });

  it("keeps a delivering rover visible but disables dragging and shows cancellation", () => {
    const wrapper = mount(RoverCard, {
      props: {
        rover: { ...baseRover, status: "delivering" as const },
        selected: false,
        deliveryId: 7,
      },
    });
    expect(wrapper.attributes("draggable")).toBe("false");
    expect(wrapper.text()).toContain("CANCEL DELIVERY");
  });
});

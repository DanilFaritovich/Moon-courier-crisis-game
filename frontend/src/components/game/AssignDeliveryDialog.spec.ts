import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssignDeliveryDialog from "./AssignDeliveryDialog.vue";

const rover = {
  id: 1,
  name: "Artemis-1",
  battery: 100,
  battery_capacity: 100,
  cargo: 0,
  cargo_capacity: 20,
  current_point_id: 1,
  status: "idle" as const,
};
const order = {
  id: 3,
  destination_point_id: 2,
  weight: 5,
  reward: 90,
  urgency: "high" as const,
  status: "available" as const,
};

describe("AssignDeliveryDialog", () => {
  it("shows the assignment preview and emits confirm", async () => {
    const wrapper = mount(AssignDeliveryDialog, {
      props: {
        rover,
        order,
        destination: {
          id: 2,
          name: "Tycho Relay",
          type: "delivery",
          x: 4,
          y: 8,
        },
        batteryAfter: 73,
        busy: false,
      },
    });

    expect(wrapper.text()).toContain("Tycho Relay");
    expect(wrapper.text()).toContain("contract #3");
    expect(wrapper.text()).toContain("100% → 73%");
    await wrapper.get(".confirm-button").trigger("click");
    expect(wrapper.emitted("confirm")).toHaveLength(1);
  });

  it("disables all actions while an assignment is being submitted", () => {
    const wrapper = mount(AssignDeliveryDialog, {
      props: { rover, order, busy: true },
    });

    expect(wrapper.text()).toContain("ASSIGNING…");
    expect(wrapper.get(".confirm-button").attributes("disabled")).toBeDefined();
    expect(wrapper.get(".quiet-button").attributes("disabled")).toBeDefined();
  });
});

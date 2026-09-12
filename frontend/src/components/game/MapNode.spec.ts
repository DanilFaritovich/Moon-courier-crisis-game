import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import type { Order } from "../../types/game";
import MapNode from "./MapNode.vue";

const point = {
  id: 2,
  name: "Crater Alpha",
  type: "delivery" as const,
  x: 10,
  y: 5,
};
const order: Order = {
  id: 3,
  destination_point_id: 2,
  weight: 4,
  reward: 80,
  urgency: "medium" as const,
  status: "available" as const,
};

function mountNode(orders = [order], valid = true) {
  return mount(MapNode, {
    props: {
      point,
      orders,
      valid,
      roverCount: 0,
      dragging: false,
      selected: false,
    },
  });
}

describe("MapNode", () => {
  it("shows full contract details for a single contract", () => {
    expect(mountNode().text()).toContain("CONTRACT #3 · ¢80 · 4 kg");
  });

  it("shows a compact count for multiple contracts", () => {
    const wrapper = mountNode([order, { ...order, id: 4 }]);
    expect(wrapper.text()).toContain("CONTRACTS ×2");
  });

  it("emits only available contracts when dropped", async () => {
    const assigned = { ...order, id: 4, status: "assigned" as const };
    const wrapper = mountNode([order, assigned]);
    await wrapper.get("g").trigger("drop");
    expect(wrapper.emitted("dropOrders")?.[0]).toEqual([[order]]);
  });

  it("does not emit a drop event for an invalid node", async () => {
    const wrapper = mountNode([order], false);
    await wrapper.get("g").trigger("drop");
    expect(wrapper.emitted("dropOrders")).toBeUndefined();
  });
});

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ContractSelectDialog from "./ContractSelectDialog.vue";

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
const orders = [
  {
    id: 1,
    destination_point_id: 2,
    weight: 3,
    reward: 60,
    urgency: "low" as const,
    status: "available" as const,
  },
  {
    id: 2,
    destination_point_id: 2,
    weight: 5,
    reward: 90,
    urgency: "high" as const,
    status: "available" as const,
  },
];

describe("ContractSelectDialog", () => {
  it("lists contracts and emits the selected order", async () => {
    const wrapper = mount(ContractSelectDialog, { props: { rover, orders } });
    expect(wrapper.text()).toContain("CONTRACT #1");
    expect(wrapper.text()).toContain("CONTRACT #2");
    await wrapper.get(".contract-row").trigger("click");
    expect(wrapper.emitted("select")?.[0]).toEqual([orders[0]]);
  });

  it("emits close when cancelled", async () => {
    const wrapper = mount(ContractSelectDialog, { props: { rover, orders } });
    await wrapper.get("footer button").trigger("click");
    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});

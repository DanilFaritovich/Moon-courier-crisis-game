import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import TopBar from "./TopBar.vue";

describe("TopBar", () => {
  it("shows game telemetry and requests the next turn", async () => {
    const wrapper = mount(TopBar, {
      props: { turn: 4, money: 125, score: 30, busy: false },
    });

    expect(wrapper.text()).toContain("TURN 4");
    expect(wrapper.text()).toContain("¢ 125");
    expect(wrapper.text()).toContain("✦ 30");
    await wrapper.get(".next-turn").trigger("click");
    expect(wrapper.emitted("nextTurn")).toHaveLength(1);
  });

  it("disables the action while the turn is processing", () => {
    const wrapper = mount(TopBar, {
      props: { turn: 4, money: 125, score: 30, busy: true },
    });

    expect(wrapper.get(".next-turn").attributes("disabled")).toBeDefined();
    expect(wrapper.text()).toContain("PROCESSING…");
  });
});

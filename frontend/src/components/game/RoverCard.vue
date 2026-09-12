<script setup lang="ts">
import type { Rover } from "../../types/game";
defineProps<{ rover: Rover; selected: boolean; deliveryId?: number }>();
defineEmits<{
  select: [Rover];
  dragStart: [Rover];
  dragEnd: [];
  cancel: [number];
}>();
const meterWidth = (current: number, maximum: number): string =>
  `${(current / maximum) * 100}%`;
</script>
<template>
  <article
    class="rover-card"
    :class="{ selected }"
    :data-testid="`rover-${rover.id}`"
    :draggable="rover.status === 'idle'"
    @click="$emit('select', rover)"
    @dragstart="rover.status === 'idle' && $emit('dragStart', rover)"
    @dragend="$emit('dragEnd')"
  >
    <div class="rover-card-head">
      <span class="rover-status" :class="rover.status" />
      <strong>{{ rover.name || `ROVER-${rover.id}` }}</strong
      ><small>#{{ rover.id }}</small>
    </div>
    <div class="meters">
      <label
        >BAT <b>{{ rover.battery }}%</b
        ><span
          ><i
            :style="{
              width: meterWidth(rover.battery, rover.battery_capacity),
            }" /></span></label
      ><label
        >CARGO <b>{{ rover.cargo }}/{{ rover.cargo_capacity }}</b
        ><span
          ><i
            :style="{
              width: meterWidth(rover.cargo, rover.cargo_capacity),
            }" /></span
      ></label>
    </div>
    <footer>
      LOC · {{ rover.current_point_id }} <em>{{ rover.status }}</em>
    </footer>
    <button
      v-if="deliveryId"
      class="cancel-delivery"
      @click.stop="$emit('cancel', deliveryId)"
    >
      CANCEL DELIVERY
    </button>
  </article>
</template>

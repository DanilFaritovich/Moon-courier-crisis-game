<script setup lang="ts">
import RoverCard from "./RoverCard.vue";
import type { Delivery, Rover } from "../../types/game";
defineProps<{
  rovers: Rover[];
  deliveries?: Delivery[];
  selectedId?: number;
}>();
defineEmits<{
  select: [Rover];
  dragStart: [Rover];
  dragEnd: [];
  cancel: [number];
}>();
</script>
<template>
  <section class="rover-dock">
    <div class="dock-label">
      <span class="eyebrow">ROVER DOCK</span><b>{{ rovers.length }} FLEET</b>
    </div>
    <div class="rover-list">
      <RoverCard
        v-for="rover in rovers"
        :key="rover.id"
        :rover="rover"
        :delivery-id="
          deliveries?.find((delivery) => delivery.rover_id === rover.id)?.id
        "
        :selected="selectedId === rover.id"
        @select="$emit('select', $event)"
        @drag-start="$emit('dragStart', $event)"
        @drag-end="$emit('dragEnd')"
        @cancel="$emit('cancel', $event)"
      />
    </div>
  </section>
</template>

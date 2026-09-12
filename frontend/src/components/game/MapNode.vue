<script setup lang="ts">
import type { MapPoint, Order } from "../../types/game";
const props = defineProps<{
  point: MapPoint;
  orders: Order[];
  roverCount: number;
  valid: boolean;
  dragging: boolean;
  selected: boolean;
}>();
const emit = defineEmits<{ select: [MapPoint]; dropOrder: [Order] }>();
function allowDrop(event: DragEvent): void {
  if (props.valid) event.preventDefault();
}
function dropOrder(event: DragEvent): void {
  event.preventDefault();
  const order = props.orders.find((item) => item.status === "available");
  if (order && props.valid) emit("dropOrder", order);
}
</script>
<template>
  <g
    class="map-node"
    :class="[
      point.type,
      {
        valid,
        selected,
        dragging,
        assigned: orders.some((order) => order.status === 'assigned'),
      },
    ]"
    @click="$emit('select', point)"
    @dragover="allowDrop"
    @drop="dropOrder"
  >
    <circle class="pulse" :cx="point.x" :cy="point.y" r="31" /><circle
      :cx="point.x"
      :cy="point.y"
      r="18"
    /><path
      v-if="point.type === 'base'"
      :d="`M ${point.x - 7} ${point.y + 5} L ${point.x} ${point.y - 7} L ${point.x + 7} ${point.y + 5} Z`"
    />
    <text class="node-name" :x="point.x" :y="point.y + 43">{{
      point.name
    }}</text
    ><text v-if="orders.length" class="order-tag" :x="point.x" :y="point.y - 38"
      >CONTRACTS ×{{ orders.length }}</text
    ><text v-if="roverCount" class="rover-tag" :x="point.x" :y="point.y + 5"
      >{{ roverCount }}R</text
    >
  </g>
</template>

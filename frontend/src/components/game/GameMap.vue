<script setup lang="ts">
import { computed, ref } from "vue";
import MapEdge from "./MapEdge.vue";
import MapNode from "./MapNode.vue";
import type { MapPoint, MapRoad, Order, Rover } from "../../types/game";

const props = defineProps<{
  points: MapPoint[];
  roads: MapRoad[];
  orders: Order[];
  rovers: Rover[];
  validOrderIds: number[];
  dragging: boolean;
  selectedPointId?: number;
}>();
defineEmits<{ selectPoint: [MapPoint]; chooseOrder: [Order] }>();
const svg = ref<SVGSVGElement>();
const view = ref({ x: 0, y: 0, width: 900, height: 560 });
const pan = ref<{ x: number; y: number; viewX: number; viewY: number }>();

const displayedPoints = computed(() => {
  if (!props.points.length) return [];
  const xs = props.points.map((point) => point.x);
  const ys = props.points.map((point) => point.y);
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const scale = Math.min(
    650 / Math.max(Math.max(...xs) - minX, 1),
    360 / Math.max(Math.max(...ys) - minY, 1),
  );
  return props.points.map((point) => ({
    ...point,
    x: 125 + (point.x - minX) * scale,
    y: 460 - (point.y - minY) * scale,
  }));
});
const viewBox = computed(
  () =>
    `${view.value.x} ${view.value.y} ${view.value.width} ${view.value.height}`,
);
const point = (id: number) =>
  displayedPoints.value.find((item) => item.id === id);
const ordersAt = (id: number) =>
  props.orders.filter((order) => order.destination_point_id === id);
function position(event: WheelEvent | PointerEvent) {
  const box = svg.value!.getBoundingClientRect();
  return {
    x:
      view.value.x +
      ((event.clientX - box.left) * view.value.width) / box.width,
    y:
      view.value.y +
      ((event.clientY - box.top) * view.value.height) / box.height,
  };
}
function zoom(event: WheelEvent) {
  event.preventDefault();
  const cursor = position(event);
  const factor = event.deltaY > 0 ? 1.15 : 0.87;
  const width = Math.min(1800, Math.max(315, view.value.width * factor));
  const height = (width * 560) / 900;
  view.value = {
    x: cursor.x - ((cursor.x - view.value.x) * width) / view.value.width,
    y: cursor.y - ((cursor.y - view.value.y) * height) / view.value.height,
    width,
    height,
  };
}
function startPan(event: PointerEvent) {
  if ((event.target as Element).closest(".map-node")) return;
  pan.value = {
    x: event.clientX,
    y: event.clientY,
    viewX: view.value.x,
    viewY: view.value.y,
  };
  (event.currentTarget as SVGSVGElement).setPointerCapture(event.pointerId);
}
function movePan(event: PointerEvent) {
  if (!pan.value || !svg.value) return;
  const box = svg.value.getBoundingClientRect();
  view.value.x =
    pan.value.viewX -
    ((event.clientX - pan.value.x) * view.value.width) / box.width;
  view.value.y =
    pan.value.viewY -
    ((event.clientY - pan.value.y) * view.value.height) / box.height;
}
</script>
<template>
  <section class="map-panel">
    <div class="map-heading">
      <span class="eyebrow">LUNAR SECTOR 07</span
      ><span>SCROLL TO ZOOM · DRAG EMPTY SPACE TO PAN</span
      ><button
        class="map-reset"
        @click="view = { x: 0, y: 0, width: 900, height: 560 }"
      >
        RESET VIEW
      </button>
    </div>
    <svg
      ref="svg"
      class="game-map"
      :viewBox="viewBox"
      @wheel="zoom"
      @pointerdown="startPan"
      @pointermove="movePan"
      @pointerup="pan = undefined"
    >
      <MapEdge
        v-for="road in roads"
        :key="`${road.from_point_id}-${road.to_point_id}`"
        :x1="point(road.from_point_id)?.x ?? 0"
        :y1="point(road.from_point_id)?.y ?? 0"
        :x2="point(road.to_point_id)?.x ?? 0"
        :y2="point(road.to_point_id)?.y ?? 0"
        :distance="road.distance"
        :risk="road.risk"
      />
      <MapNode
        v-for="mapPoint in displayedPoints"
        :key="mapPoint.id"
        :point="mapPoint"
        :orders="ordersAt(mapPoint.id)"
        :rover-count="
          rovers.filter((rover) => rover.current_point_id === mapPoint.id)
            .length
        "
        :valid="
          ordersAt(mapPoint.id).some((order) =>
            validOrderIds.includes(order.id),
          )
        "
        :dragging="dragging"
        :selected="selectedPointId === mapPoint.id"
        @select="$emit('selectPoint', $event)"
        @drop-order="$emit('chooseOrder', $event)"
      />
    </svg>
  </section>
</template>

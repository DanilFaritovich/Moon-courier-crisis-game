<script setup lang="ts">
import MapEdge from './MapEdge.vue'
import MapNode from './MapNode.vue'
import type { MapPoint, MapRoad, Order, Rover } from '../../types/game'
const props = defineProps<{ points: MapPoint[]; roads: MapRoad[]; orders: Order[]; rovers: Rover[]; validOrderIds: number[]; dragging: boolean; selectedPointId?: number }>()
defineEmits<{ selectPoint: [MapPoint]; chooseOrder: [Order] }>()
const point = (id: number) => props.points.find((item) => item.id === id)
const orderAt = (id: number) => props.orders.find((order) => order.destination_point_id === id)
</script>
<template>
  <section class="map-panel"><div class="map-heading"><span class="eyebrow">LUNAR SECTOR 07</span><span v-if="dragging" class="drop-hint">DROP ON A HIGHLIGHTED CONTRACT</span><span v-else>SELECT A POINT OR DEPLOY A ROVER</span></div><svg class="game-map" viewBox="0 0 900 560" role="img" aria-label="Lunar delivery map"><defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="currentColor" stroke-width=".5" /></pattern></defs><rect width="900" height="560" fill="url(#grid)" /><MapEdge v-for="road in roads" :key="`${road.from_point_id}-${road.to_point_id}`" :x1="point(road.from_point_id)?.x ?? 0" :y1="point(road.from_point_id)?.y ?? 0" :x2="point(road.to_point_id)?.x ?? 0" :y2="point(road.to_point_id)?.y ?? 0" :distance="road.distance" :risk="road.risk" /><MapNode v-for="mapPoint in points" :key="mapPoint.id" :point="mapPoint" :order="orderAt(mapPoint.id)" :rover-count="rovers.filter((rover) => rover.current_point_id === mapPoint.id).length" :valid="Boolean(orderAt(mapPoint.id) && validOrderIds.includes(orderAt(mapPoint.id)!.id))" :dragging="dragging" :selected="selectedPointId === mapPoint.id" @select="$emit('selectPoint', $event)" @drop-order="$emit('chooseOrder', $event)" /></svg><div class="map-legend"><span><i class="base-dot" /> BASE</span><span><i class="delivery-dot" /> DELIVERY</span><span><i class="contract-dot" /> ACTIVE CONTRACT</span></div></section>
</template>

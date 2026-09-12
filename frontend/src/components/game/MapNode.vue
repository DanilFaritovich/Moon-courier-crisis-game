<script setup lang="ts">
import type { MapPoint, Order } from '../../types/game'
const props = defineProps<{ point: MapPoint; order?: Order; roverCount: number; valid: boolean; dragging: boolean; selected: boolean }>()
const emit = defineEmits<{ select: [MapPoint]; dropOrder: [Order] }>()
function allowDrop(event: DragEvent): void { if (props.valid) event.preventDefault() }
function dropOrder(event: DragEvent): void { event.preventDefault(); if (props.order && props.valid) emit('dropOrder', props.order) }
</script>
<template>
  <g class="map-node" :class="[point.type, { valid, selected, dragging }]" @click="$emit('select', point)" @dragover="allowDrop" @drop="dropOrder">
    <circle class="pulse" :cx="point.x" :cy="point.y" r="31" /><circle :cx="point.x" :cy="point.y" r="18" /><path v-if="point.type === 'base'" :d="`M ${point.x - 7} ${point.y + 5} L ${point.x} ${point.y - 7} L ${point.x + 7} ${point.y + 5} Z`" />
    <text class="node-name" :x="point.x" :y="point.y + 43">{{ point.name }}</text><text v-if="order" class="order-tag" :x="point.x" :y="point.y - 38">ORDER #{{ order.id }} · ¢{{ order.reward }}</text><text v-if="roverCount" class="rover-tag" :x="point.x" :y="point.y + 5">{{ roverCount }}R</text>
  </g>
</template>

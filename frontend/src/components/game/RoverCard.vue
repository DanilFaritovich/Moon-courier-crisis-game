<script setup lang="ts">
import type { Rover } from '../../types/game'
defineProps<{ rover: Rover; selected: boolean }>()
defineEmits<{ select: [Rover]; dragStart: [Rover]; dragEnd: [] }>()
const meterWidth = (current: number, maximum: number): string => `${(current / maximum) * 100}%`
</script>
<template>
  <article class="rover-card" :class="{ selected }" draggable="true" @click="$emit('select', rover)" @dragstart="$emit('dragStart', rover)" @dragend="$emit('dragEnd')"><div class="rover-card-head"><span class="rover-status" :class="rover.status" /> <strong>{{ rover.name || `ROVER-${rover.id}` }}</strong><small>#{{ rover.id }}</small></div><div class="meters"><label>BAT <b>{{ rover.battery }}%</b><span><i :style="{ width: meterWidth(rover.battery, rover.battery_capacity) }" /></span></label><label>CARGO <b>{{ rover.cargo }}/{{ rover.cargo_capacity }}</b><span><i :style="{ width: meterWidth(rover.cargo, rover.cargo_capacity) }" /></span></label></div><footer>LOC · {{ rover.current_point_id }} <em>{{ rover.status }}</em></footer></article>
</template>

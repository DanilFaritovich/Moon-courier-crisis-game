<script setup lang="ts">
import RoverCard from './RoverCard.vue'
import type { Rover } from '../../types/game'
defineProps<{ rovers: Rover[]; selectedId?: number }>()
defineEmits<{ select: [Rover]; dragStart: [Rover]; dragEnd: [] }>()
</script>
<template><section class="rover-dock"><div class="dock-label"><span class="eyebrow">ROVER DOCK</span><b>{{ rovers.length }} READY</b></div><div class="rover-list"><RoverCard v-for="rover in rovers" :key="rover.id" :rover="rover" :selected="selectedId === rover.id" @select="$emit('select', $event)" @drag-start="$emit('dragStart', $event)" @drag-end="$emit('dragEnd')" /></div></section></template>

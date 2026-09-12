<script setup lang="ts">
import type { Order, Rover } from "../../types/game";
defineProps<{ rover: Rover; orders: Order[] }>();
defineEmits<{ select: [Order]; close: [] }>();
</script>
<template>
  <div class="dialog-backdrop">
    <section class="delivery-dialog">
      <span class="eyebrow">SELECT CONTRACT</span>
      <h2>{{ rover.name }} is ready</h2>
      <p>Choose a contract for this destination.</p>
      <button
        v-for="order in orders"
        :key="order.id"
        class="quiet-button contract-choice"
        :disabled="order.status !== 'available'"
        @click="$emit('select', order)"
      >
        CONTRACT #{{ order.id }} · ¢{{ order.reward }} · {{ order.weight }} kg
      </button>
      <footer>
        <button class="quiet-button" @click="$emit('close')">CANCEL</button>
      </footer>
    </section>
  </div>
</template>

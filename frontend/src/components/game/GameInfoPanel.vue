<script setup lang="ts">
import type { Delivery, MapPoint, Order, Rover } from "../../types/game";

defineProps<{
  point?: MapPoint;
  rover?: Rover;
  orders?: Order[];
  delivery?: Delivery;
  locationName?: string;
  destinationName?: string;
}>();
defineEmits<{ cancel: [number]; chooseOrder: [Order] }>();
</script>

<template>
  <aside class="info-panel">
    <span class="eyebrow">TACTICAL INFO</span>

    <template v-if="rover">
      <h2>{{ rover.name }}</h2>
      <p class="entity-type">ROVER #{{ rover.id }} · {{ rover.status }}</p>
      <dl>
        <div>
          <dt>BATTERY</dt>
          <dd>{{ rover.battery }} / {{ rover.battery_capacity }}%</dd>
        </div>
        <div>
          <dt>CARGO</dt>
          <dd>{{ rover.cargo }} / {{ rover.cargo_capacity }} kg</dd>
        </div>
        <div>
          <dt>LOCATION</dt>
          <dd>{{ locationName ?? `POINT ${rover.current_point_id}` }}</dd>
        </div>
        <div v-if="delivery">
          <dt>ACTIVE CONTRACT</dt>
          <dd>#{{ delivery.order_id }}</dd>
        </div>
        <div v-if="delivery">
          <dt>DESTINATION</dt>
          <dd>{{ destinationName ?? "Unknown" }}</dd>
        </div>
      </dl>
      <button
        v-if="delivery"
        class="quiet-button"
        @click="$emit('cancel', delivery.id)"
      >
        CANCEL DELIVERY
      </button>
    </template>

    <template v-else-if="point">
      <h2>{{ point.name }}</h2>
      <p class="entity-type">
        {{ point.type === "base" ? "LUNAR BASE" : `${point.type} POINT` }}
      </p>
      <dl>
        <div v-for="order in orders" :key="order.id">
          <dt>CONTRACT #{{ order.id }}</dt>
          <dd>
            <button
              class="contract-choice"
              :disabled="order.status !== 'available'"
              @click="$emit('chooseOrder', order)"
            >
              ¢{{ order.reward }} · {{ order.weight }} kg · {{ order.status }}
            </button>
          </dd>
        </div>
      </dl>
      <p v-if="!orders?.length" class="entity-type">
        No active contract at this point.
      </p>
    </template>

    <div v-else class="empty-info">
      <span>◌</span>
      <p>Select a rover or map point.</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { gameApi } from "../api/game";
import AssignDeliveryDialog from "../components/game/AssignDeliveryDialog.vue";
import ContractSelectDialog from "../components/game/ContractSelectDialog.vue";
import GameInfoPanel from "../components/game/GameInfoPanel.vue";
import GameMap from "../components/game/GameMap.vue";
import RoverDock from "../components/game/RoverDock.vue";
import TopBar from "../components/layout/TopBar.vue";
import type {
  AvailableOrder,
  GameState,
  MapPoint,
  MapRoad,
  Order,
  Rover,
} from "../types/game";

const state = ref<GameState>();
const points = ref<MapPoint[]>([]);
const roads = ref<MapRoad[]>([]);
const selectedRover = ref<Rover>();
const selectedPoint = ref<MapPoint>();
const draggingRover = ref<Rover>();
const validOrderIds = ref<number[]>([]);
const previews = ref<AvailableOrder[]>([]);
const assignment = ref<{ rover: Rover; order: Order }>();
const contractChoices = ref<Order[]>();
const contractChoiceRover = ref<Rover>();
const busy = ref(false);
const error = ref("");
const rovers = computed(() => state.value?.active_rovers ?? []);
const selectedPointOrders = computed(() =>
  selectedPoint.value
    ? (state.value?.active_orders.filter(
        (order) => order.destination_point_id === selectedPoint.value?.id,
      ) ?? [])
    : [],
);
const selectedDelivery = computed(() =>
  selectedRover.value
    ? state.value?.active_deliveries.find(
        (delivery) => delivery.rover_id === selectedRover.value?.id,
      )
    : undefined,
);
const selectedLocationName = computed(() =>
  selectedRover.value
    ? points.value.find(
        (point) => point.id === selectedRover.value?.current_point_id,
      )?.name
    : undefined,
);
const selectedDestinationName = computed(() => {
  const order = state.value?.active_orders.find(
    (item) => item.id === selectedDelivery.value?.order_id,
  );
  return points.value.find((point) => point.id === order?.destination_point_id)
    ?.name;
});

function messageFromError(caught: unknown, fallback: string): string {
  if (caught instanceof TypeError) {
    return "Mission Control is unreachable. Check the backend and retry.";
  }
  return caught instanceof Error ? caught.message : fallback;
}

async function loadGame(): Promise<void> {
  busy.value = true;
  error.value = "";
  try {
    const [game, map] = await Promise.all([gameApi.state(), gameApi.map()]);
    state.value = game;
    points.value = map.points;
    roads.value = map.roads;
  } catch (caught) {
    error.value = messageFromError(caught, "Could not load the game.");
  } finally {
    busy.value = false;
  }
}

async function perform(action: () => Promise<GameState>): Promise<void> {
  busy.value = true;
  error.value = "";
  try {
    state.value = await action();
    if (selectedRover.value) {
      selectedRover.value = state.value.active_rovers.find(
        (rover) => rover.id === selectedRover.value?.id,
      );
    }
  } catch (caught) {
    error.value = messageFromError(caught, "Action failed.");
  } finally {
    busy.value = false;
  }
}

async function startDrag(rover: Rover): Promise<void> {
  if (rover.status !== "idle") return;
  selectedRover.value = rover;
  draggingRover.value = rover;
  try {
    previews.value = await gameApi.availableOrders(rover.id);
    validOrderIds.value = previews.value.map((order) => order.id);
  } catch (caught) {
    error.value = messageFromError(caught, "Could not load contracts.");
    endDrag();
  }
}
function endDrag(): void {
  draggingRover.value = undefined;
  validOrderIds.value = [];
}
function selectPoint(point: MapPoint): void {
  selectedPoint.value = point;
  selectedRover.value = undefined;
}
function selectOrder(order: Order): void {
  if (draggingRover.value && validOrderIds.value.includes(order.id)) {
    assignment.value = { rover: draggingRover.value, order };
    endDrag();
  }
}
function chooseOrders(orders: Order[]): void {
  const available = orders.filter((order) =>
    validOrderIds.value.includes(order.id),
  );
  if (!available.length || !draggingRover.value) return;
  if (available.length === 1) {
    assignment.value = { rover: draggingRover.value, order: available[0] };
    endDrag();
    return;
  }
  contractChoiceRover.value = draggingRover.value;
  contractChoices.value = available;
  endDrag();
}
function selectContract(order: Order): void {
  if (contractChoiceRover.value) {
    assignment.value = { rover: contractChoiceRover.value, order };
  }
  contractChoices.value = undefined;
  contractChoiceRover.value = undefined;
}
async function confirmDelivery(): Promise<void> {
  if (assignment.value)
    await perform(async () => {
      const result = await gameApi.createDelivery(
        assignment.value!.rover.id,
        assignment.value!.order.id,
      );
      assignment.value = undefined;
      return result;
    });
}
async function cancelDelivery(deliveryId: number): Promise<void> {
  await perform(() => gameApi.cancelDelivery(deliveryId));
}
onMounted(loadGame);
</script>

<template>
  <main class="game-shell">
    <TopBar
      :turn="state?.turn ?? 0"
      :money="state?.money ?? 0"
      :score="state?.score ?? 0"
      :busy="busy"
      @next-turn="perform(gameApi.nextTurn)"
    />
    <p v-if="error" class="notification" role="alert">{{ error }}</p>
    <div v-if="!state" class="center-state">
      <span>{{
        error ? "MISSION CONTROL OFFLINE" : "CONNECTING TO MISSION CONTROL…"
      }}</span>
      <button v-if="error" class="quiet-button" @click="loadGame">
        RETRY CONNECTION
      </button>
    </div>
    <template v-else>
      <div class="mission-grid">
        <GameMap
          :points="points"
          :roads="roads"
          :orders="state.active_orders"
          :rovers="rovers"
          :valid-order-ids="validOrderIds"
          :dragging="Boolean(draggingRover)"
          @select-point="selectPoint"
          @choose-orders="chooseOrders"
        />
        <GameInfoPanel
          :rover="selectedRover"
          :point="selectedRover ? undefined : selectedPoint"
          :orders="selectedPointOrders"
          :deliveries="state.active_deliveries"
          :delivery="selectedDelivery"
          :location-name="selectedLocationName"
          :destination-name="selectedDestinationName"
          @cancel="cancelDelivery"
          @choose-order="selectOrder"
        />
      </div>
      <RoverDock
        :rovers="rovers"
        :deliveries="state.active_deliveries"
        :selected-id="selectedRover?.id"
        @select="selectedRover = $event"
        @drag-start="startDrag"
        @drag-end="endDrag"
        @cancel="perform(() => gameApi.cancelDelivery($event))"
      />
    </template>
    <AssignDeliveryDialog
      v-if="assignment"
      :rover="assignment.rover"
      :order="assignment.order"
      :destination="
        points.find(
          (point) => point.id === assignment?.order.destination_point_id,
        )
      "
      :battery-after="
        previews.find((order) => order.id === assignment?.order.id)
          ?.battery_after
      "
      :busy="busy"
      @confirm="confirmDelivery"
      @close="assignment = undefined"
    />
    <ContractSelectDialog
      v-if="contractChoices && contractChoiceRover"
      :rover="contractChoiceRover"
      :orders="contractChoices"
      @select="selectContract"
      @close="
        contractChoices = undefined;
        contractChoiceRover = undefined;
      "
    />
  </main>
</template>

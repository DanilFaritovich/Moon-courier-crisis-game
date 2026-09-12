export type PointType = 'base' | 'delivery' | 'route'
export type RoverStatus = 'idle' | 'delivering' | 'charging' | 'disabled'
export type OrderStatus = 'available' | 'assigned' | 'completed'
export type OrderUrgency = 'low' | 'medium' | 'high'

export interface Rover {
  id: number
  name: string
  cargo_capacity: number
  cargo: number
  battery_capacity: number
  battery: number
  current_point_id: number
  status: RoverStatus
}

export interface Order {
  id: number
  destination_point_id: number
  weight: number
  reward: number
  urgency: OrderUrgency
  status: OrderStatus
}

export interface Delivery {
  id: number
  order_id: number
  rover_id: number
  status: 'in_progress' | 'completed' | 'failed'
  started_turn: number
  completed_turn: number | null
}

export interface GameState {
  game_id: string
  active_rovers: Rover[]
  active_orders: Order[]
  active_deliveries: Delivery[]
  active_events: Array<{ id: number; event_type: string; title: string; description: string; start_turn: number; end_turn: number }>
  turn: number
  money: number
  score: number
}

export interface MapPoint { id: number; name: string; type: PointType; x: number; y: number }
export interface MapRoad { from_point_id: number; to_point_id: number; distance: number; risk: number; speed_modifier: number }

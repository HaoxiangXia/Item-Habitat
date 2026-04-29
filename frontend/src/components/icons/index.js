import { h } from 'vue'

const createIcon = (svgPaths, viewBox = "0 0 24 24") => {
  return {
    render() {
      const attrs = this.$attrs || {}
      const { size, ...restAttrs } = attrs
      const svgProps = {
        viewBox,
        width: size || "24",
        height: size || "24",
        fill: "none",
        stroke: "currentColor",
        "stroke-width": "2",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        ...restAttrs
      }

      return h('svg', svgProps, svgPaths)
    }
  }
}

export const HomeIcon = createIcon([
  h('path', { d: "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" }),
  h('polyline', { points: "9 22 9 12 15 12 15 22" })
])

export const ChevronDownIcon = createIcon([
  h('polyline', { points: "6 9 12 15 18 9" })
])

export const ChevronRightIcon = createIcon([
  h('polyline', { points: "9 18 15 12 9 6" })
])

export const ArrowDownIcon = createIcon([
  h('line', { x1: "12", y1: "5", x2: "12", y2: "19" }),
  h('polyline', { points: "19 12 12 19 5 12" })
])

export const ArrowUpIcon = createIcon([
  h('line', { x1: "12", y1: "19", x2: "12", y2: "5" }),
  h('polyline', { points: "5 12 12 5 19 12" })
])

export const SearchIcon = createIcon([
  h('circle', { cx: "11", cy: "11", r: "8" }),
  h('line', { x1: "21", y1: "21", x2: "16.65", y2: "16.65" })
])

export const ClockIcon = createIcon([
  h('circle', { cx: "12", cy: "12", r: "10" }),
  h('polyline', { points: "12 6 12 12 16 14" })
])

export const MapIcon = createIcon([
  h('polygon', { points: "1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" }),
  h('line', { x1: "8", y1: "2", x2: "8", y2: "18" }),
  h('line', { x1: "16", y1: "6", x2: "16", y2: "22" })
])

export const MenuIcon = createIcon([
  h('line', { x1: "3", y1: "12", x2: "21", y2: "12" }),
  h('line', { x1: "3", y1: "6", x2: "21", y2: "6" }),
  h('line', { x1: "3", y1: "18", x2: "21", y2: "18" })
])

export const PlusIcon = createIcon([
  h('line', { x1: "12", y1: "5", x2: "12", y2: "19" }),
  h('line', { x1: "5", y1: "12", x2: "19", y2: "12" })
])

export const XIcon = createIcon([
  h('line', { x1: "6", y1: "6", x2: "18", y2: "18" }),
  h('line', { x1: "6", y1: "18", x2: "18", y2: "6" })
])

export const PackageIcon = createIcon([
  h('path', { d: "M3 7l9-4 9 4-9 4-9-4z" }),
  h('path', { d: "M3 7v10l9 4 9-4V7" }),
  h('path', { d: "M12 11v10" })
])

export const TrendIcon = createIcon([
  h('path', { d: "M3 17l6-6 4 4 8-8" }),
  h('path', { d: "M14 7h7v7" })
])

export const HistoryIcon = createIcon([
  h('circle', { cx: "12", cy: "12", r: "9" }),
  h('path', { d: "M12 7v5l3 2" })
])

export const LayersIcon = createIcon([
  h('path', { d: "M12 4l9 5-9 5-9-5 9-5z" }),
  h('path', { d: "M3 14l9 5 9-5" }),
  h('path', { d: "M3 10l9 5 9-5" })
])

export const CheckIcon = createIcon([
  h('polyline', { points: "20 6 9 17 4 12" })
])

export const BackIcon = createIcon([
  h('line', { x1: "19", y1: "12", x2: "5", y2: "12" }),
  h('polyline', { points: "12 19 5 12 12 5" })
])

export const ReceiptIcon = createIcon([
  h('path', { d: "M6 3h12v18l-2-1.2-2 1.2-2-1.2-2 1.2-2-1.2-2 1.2z" }),
  h('path', { d: "M8 8h8" }),
  h('path', { d: "M8 12h8" }),
  h('path', { d: "M8 16h5" })
])

<template>
  <div :id="circleId" class="js-circle"></div>
</template>

<script>
let circleIdCounter = 0;
export default {
  name: 'CircleGraph',
  props: {
    value: {
      type: Number,
      required: true
    },
    maxValue: {
      type: Number,
      default: 100
    },
    label: {
      type: String,
      default: ''
    },
    colorMode: {
      type: String,
      default: 'medicare' // 'medicare' for IRMAA color logic, 'fixed' for a single color
    },
    fixedColor: {
      type: String,
      default: '#377dff'
    },
    radius: {
      type: Number,
      default: 70
    },
    width: {
      type: Number,
      default: 20
    }
  },
  data() {
    return {
      circleId: 'circle-graph-' + (++circleIdCounter)
    };
  },
  watch: {
    value: 'renderCircle',
    maxValue: 'renderCircle',
    colorMode: 'renderCircle',
    fixedColor: 'renderCircle'
  },
  mounted() {
    this.renderCircle();
  },
  methods: {
    getColor() {
      if (this.colorMode === 'medicare') {
        // Medicare IRMAA color logic
        if (this.value > 50) {
          return '#ff0000';
        } else if (this.value > 25) {
          return '#ffa500';
        } else if (this.value > 15) {
          return '#ffff00';
        } else {
          return '#00ff00';
        }
      } else {
        return this.fixedColor;
      }
    },
    renderCircle() {
      this.$nextTick(() => {
        const CirclesGlobal = window.Circles;
        const el = document.getElementById(this.circleId);
        if (!CirclesGlobal || !el) return;
        // Clear previous SVG if any (safe operation - not user input)
        while (el.firstChild) {
          el.removeChild(el.firstChild);
        }
        CirclesGlobal.create({
          id: this.circleId,
          value: Math.round(this.value),
          maxValue: this.maxValue,
          width: this.width,
          radius: this.radius,
          text: (val) => (this.label ? this.label : val + '%'),
          colors: ['#f0f0f0', this.getColor()],
          duration: 400,
          wrpClass: 'circles-wrp',
          textClass: 'circles-text',
          styleWrapper: true,
          styleText: true
        });
      });
    }
  }
};
</script>

<style scoped>
.js-circle {
  min-width: 160px;
  min-height: 160px;
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 
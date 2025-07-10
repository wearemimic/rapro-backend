<template>
  <div class="card h-100">
    <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
      <h5 class="mb-0">Asset Selection Panel</h5>
    </div>
    <div class="card-body">
      <div class="table-responsive">
        <table class="table table-bordered table-hover align-middle">
          <thead class="thead-light">
            <tr>
              <th>Asset</th>
              <th>Owner</th>
              <th>Current Value</th>
              <th>Max to Convert</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asset in (eligibleAssets && eligibleAssets.length ? eligibleAssets : [])" :key="asset.id || asset.income_type">
              <td>{{ asset.income_type || 'Unknown' }}</td>
              <td>{{ asset.owned_by || 'Unknown' }}</td>
              <td>{{ formatCurrency(asset.current_asset_balance) }}</td>
              <td>
                <input
                  type="text"
                  :value="maxToConvertRaw[asset.id || asset.income_type] || ''"
                  @focus="onMaxToConvertFocus(asset)"
                  @input="onMaxToConvertInput($event, asset)"
                  @blur="onMaxToConvertBlur(asset)"
                  class="form-control form-control-sm"
                />
              </td>
            </tr>
            <!-- Total Row -->
            <tr style="font-weight: bold; background: #f8f9fa;">
              <td>Total to Convert</td>
              <td></td>
              <td></td>
              <td>{{ formatCurrency(totalToConvert) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetSelectionPanel',
  props: {
    eligibleAssets: {
      type: Array,
      required: true
    },
    maxToConvert: {
      type: Object,
      required: true
    },
    maxToConvertRaw: {
      type: Object,
      required: true
    },
    headerColor: {
      type: String,
      default: '#377dff'
    }
  },
  emits: ['update:maxToConvert', 'update:maxToConvertRaw'],
  computed: {
    totalToConvert() {
      return (this.eligibleAssets || []).reduce((sum, asset) => {
        const val = this.maxToConvert[asset.id || asset.income_type];
        return sum + (parseFloat(val) || 0);
      }, 0);
    }
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value || 0);
    },
    onMaxToConvertFocus(asset) {
      const key = asset.id || asset.income_type;
      const val = this.maxToConvert[key];
      let newRaw = (!val || val === 0) ? '' : val.toString();
      this.$emit('update:maxToConvertRaw', { ...this.maxToConvertRaw, [key]: newRaw });
    },
    onMaxToConvertInput(event, asset) {
      const key = asset.id || asset.income_type;
      let raw = event.target.value.replace(/[^0-9.]/g, '');
      const parts = raw.split('.');
      if (parts.length > 2) raw = parts[0] + '.' + parts[1];
      if (parts[1]) raw = parts[0] + '.' + parts[1].slice(0, 2);
      if (raw === '.') {
        this.$emit('update:maxToConvertRaw', { ...this.maxToConvertRaw, [key]: '0.' });
        this.$emit('update:maxToConvert', { ...this.maxToConvert, [key]: 0 });
        return;
      }
      if (raw === '') {
        this.$emit('update:maxToConvertRaw', { ...this.maxToConvertRaw, [key]: '' });
        this.$emit('update:maxToConvert', { ...this.maxToConvert, [key]: 0 });
        return;
      }
      let numeric = parseFloat(raw);
      if (isNaN(numeric)) numeric = 0;
      const max = parseFloat(asset.current_asset_balance) || 0;
      if (numeric > max) {
        numeric = max;
      }
      const [intPart, decPart] = numeric.toString().split('.');
      let formatted = parseInt(intPart, 10).toLocaleString();
      if (decPart !== undefined) {
        formatted += '.' + decPart;
      }
      this.$emit('update:maxToConvertRaw', { ...this.maxToConvertRaw, [key]: formatted });
      this.$emit('update:maxToConvert', { ...this.maxToConvert, [key]: numeric });
    },
    onMaxToConvertBlur(asset) {
      const key = asset.id || asset.income_type;
      const val = this.maxToConvert[key];
      this.$emit('update:maxToConvertRaw', { ...this.maxToConvertRaw, [key]: this.formatCurrency(val) });
    }
  }
};
</script> 
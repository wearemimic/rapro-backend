import { mount } from '@vue/test-utils';
import ScenarioCreate from '@/views/ScenarioCreate.vue';

describe('ScenarioCreate.vue', () => {
  it('renders the scenario form', () => {
    const wrapper = mount(ScenarioCreate, {
      global: {
        stubs: ['router-link', 'router-view']
      }
    });
    expect(wrapper.text()).toContain('Create New Scenario');
  });
});
import { strict as assert } from 'node:assert';
import { test } from 'node:test';

import {
  cadSystemAvailability,
  cadSystemDescriptor,
  DEFAULT_CAD_SYSTEM,
  isCadSystem,
  listCadSystems,
} from '../src/cad-systems.ts';

test('registers only the public a3d-text system', () => {
  assert.deepEqual(listCadSystems(), ['a3d-text']);
  assert.equal(DEFAULT_CAD_SYSTEM, 'a3d-text');
  assert.equal(isCadSystem('a3d-text'), true);
  assert.equal(isCadSystem('a3d-blender'), false);
  assert.equal(isCadSystem(undefined), false);
  assert.equal(isCadSystem(null), false);
});

test('describes the default system paths and requirements', () => {
  const descriptor = cadSystemDescriptor();
  assert.equal(descriptor.id, 'a3d-text');
  assert.equal(descriptor.skillDirectoryName, 'a3d-text');
  assert.equal(descriptor.runtimeDirectoryName, 'a3d-public');
  assert.deepEqual(descriptor.requirements, ['python']);
  assert.equal(cadSystemDescriptor('a3d-text'), descriptor);
});

test('reports availability only when runtime and python are ready', () => {
  assert.deepEqual(
    cadSystemAvailability('a3d-text', {
      pythonReady: true,
      runtimeReady: true,
    }),
    { ready: true, requirements: ['python'] },
  );
  const missingPython = cadSystemAvailability('a3d-text', {
    pythonReady: false,
    runtimeReady: true,
  });
  assert.equal(missingPython.ready, false);
  assert.match(missingPython.error ?? '', /Python CAD runtime is not ready/u);
  const missingRuntime = cadSystemAvailability('a3d-text', {
    pythonReady: true,
    runtimeError: 'LLM_API_KEY is not configured in .env.',
    runtimeReady: false,
  });
  assert.equal(missingRuntime.ready, false);
  assert.equal(missingRuntime.error, 'LLM_API_KEY is not configured in .env.');
});

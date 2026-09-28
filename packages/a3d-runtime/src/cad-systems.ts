export type CadRuntimeRequirement = 'python';
export type CadSystem = 'a3d-text';

export interface CadSystemDescriptor {
  readonly description: string;
  readonly id: CadSystem;
  readonly requirements: readonly CadRuntimeRequirement[];
  readonly runtimeDirectoryName: string;
  readonly skillDirectoryName: string;
  /** Extra system prompt segment for CAD turns; omitted when the public default needs none. */
  readonly systemInstruction?: string;
}

export interface CadSystemAvailability {
  readonly error?: string;
  readonly ready: boolean;
  readonly requirements: readonly CadRuntimeRequirement[];
}

export const DEFAULT_CAD_SYSTEM: CadSystem = 'a3d-text';

const CAD_SYSTEMS = {
  'a3d-text': {
    description: 'Create and validate printable 3D models with the project a3d CLI.',
    id: 'a3d-text',
    requirements: ['python'],
    runtimeDirectoryName: 'a3d-public',
    skillDirectoryName: 'a3d-text',
  },
} as const satisfies Record<CadSystem, CadSystemDescriptor>;

export function isCadSystem(value: unknown): value is CadSystem {
  return value === 'a3d-text';
}

export function cadSystemDescriptor(
  system: CadSystem = DEFAULT_CAD_SYSTEM,
): CadSystemDescriptor {
  return CAD_SYSTEMS[system];
}

export function listCadSystems(): readonly CadSystem[] {
  return Object.keys(CAD_SYSTEMS) as CadSystem[];
}

export function cadSystemAvailability(
  system: CadSystem,
  status: {
    readonly runtimeError?: string;
    readonly runtimeReady: boolean;
    readonly pythonReady: boolean;
  },
): CadSystemAvailability {
  const descriptor = cadSystemDescriptor(system);
  const ready = status.runtimeReady && status.pythonReady;
  return {
    ...(!ready
      ? {
          error:
            status.runtimeError ||
            (descriptor.requirements.includes('python')
              ? 'Python CAD runtime is not ready.'
              : 'CAD runtime is not ready.'),
        }
      : {}),
    ready,
    requirements: descriptor.requirements,
  };
}

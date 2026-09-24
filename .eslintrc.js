module.exports = {
    root: true,
    env: {
        node: true,
    },
    extends: [
        'plugin:vue/vue3-essential',
        'eslint:recommended',
        '@vue/eslint-config-typescript',
		'plugin:vuejs-accessibility/recommended',
    ],
    rules: {
        'indent': 'off',
        'prefer-const': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-unused-vars': 'off',
        '@typescript-eslint/no-unsafe-function-type': 'off',
        '@typescript-eslint/no-unused-expressions': [
            'error',
            {
                allowShortCircuit: true,
                allowTernary: true,
            },
        ],
        'vue/multi-word-component-names': 'off',
		'vuejs-accessibility/label-has-for': [
			'error',
			{
				components: ['Label'],
				controlComponents: ['VCheckbox', 'VTextField', 'VSelect', 'VSwitch'],
				required: {
				some: ['nesting', 'id'],
				},
				allowChildren: false,
			},
		],
		'vue/no-side-effects-in-computed-properties': 'off',
		'vue/valid-v-slot': 'off',
		'vue/no-mutating-props': 'off',
    },
}

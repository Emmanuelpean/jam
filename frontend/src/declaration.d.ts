declare module "*.svg" {
	import * as React from "react";

	// for importing as a React component
	export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement> & { title?: string }>;

	// for importing as a URL (e.g. in <img src="..." />)
	const src: string;
	export default src;
}

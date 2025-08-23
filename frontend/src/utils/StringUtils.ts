export function pluralize(word: string) {
	// Handle common irregular nouns
	const irregulars = {
		child: "children",
		man: "men",
		woman: "women",
		person: "people",
		mouse: "mice",
		goose: "geese",
		foot: "feet",
		tooth: "teeth",
		ox: "oxen",
	};

	if (irregulars[word.toLowerCase()]) {
		return irregulars[word.toLowerCase()];
	}

	// Handle basic rules
	if (word.endsWith("y") && !/[aeiou]y$/i.test(word)) {
		return word.slice(0, -1) + "ies";
	} else if (
		word.endsWith("s") ||
		word.endsWith("x") ||
		word.endsWith("z") ||
		word.endsWith("ch") ||
		word.endsWith("sh")
	) {
		return word + "es";
	} else if (word.endsWith("f")) {
		return word.slice(0, -1) + "ves";
	} else if (word.endsWith("fe")) {
		return word.slice(0, -2) + "ves";
	} else {
		return word + "s";
	}
}

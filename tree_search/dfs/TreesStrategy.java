package verification;

import java.util.ArrayList;
import java.util.HashMap;

/**
 *
 * @author Michael Albert
 */
public class TreesStrategy {

    private Node[] nodes;

    public TreesStrategy(Node[] nodes) {
        this.nodes = nodes;

        boolean changed = true;
        while (changed) {
            changed = false;
            for (int i = 0; i < nodes.length; i++) {
                if (!nodes[i].isVerified && !nodes[i].isUnverifiable()) {
                    TreeStrategy t = new TreeStrategy(nodes[i], nodes);
                    boolean foundTree = t.run();
                    if (foundTree) {
                        // System.out.println("Found a tree");
                        changed = true;
                        HashMap<Node, ArrayList<Node>> v = t.getVerification();
                        for (Node n : v.keySet()) {
                            n.isVerified = true;
                            n.verifier = v.get(n);
                        }
                    }
                }
            }

        }
        for (int i = 0; i < nodes.length; i++) {
            if (nodes[i].isVerified) System.out.println(nodes[i]);

        }
    }

}
